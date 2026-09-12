import os
from datetime import datetime

from dotenv import load_dotenv
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Boolean,
    ForeignKey,
    DateTime,
    UniqueConstraint,
)
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

LOCAL_DATABASE_URL = os.getenv(
    "LOCAL_DATABASE_URL",
    "postgresql://postgres:postgres@localhost:15432/game_db",
)

engine = create_engine(LOCAL_DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Player(Base):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    score = Column(Integer, default=0)


class Scenario(Base):
    __tablename__ = "scenarios"

    id = Column(Integer, primary_key=True, index=True)
    npc_name = Column(String)
    description = Column(String)


class Action(Base):
    __tablename__ = "actions"

    id = Column(Integer, primary_key=True, index=True)
    scenario_id = Column(Integer, ForeignKey("scenarios.id"))
    action_text = Column(String)
    is_correct = Column(Boolean)
    points_modifier = Column(Integer)
    animal_message = Column(String)


class PlayerProgress(Base):
    __tablename__ = "player_progress"

    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"))
    scenario_id = Column(Integer, ForeignKey("scenarios.id"))
    action_taken_id = Column(Integer, ForeignKey("actions.id"))
    completed_at = Column(DateTime, default=datetime.utcnow)


class ArcadeScore(Base):
    __tablename__ = "arcade_scores"

    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    level_number = Column(Integer, nullable=False)
    best_score = Column(Integer, nullable=False, default=0)

    __table_args__ = (
        UniqueConstraint(
            "player_id",
            "level_number",
            name="uq_player_arcade_level",
        ),
    )


Base.metadata.create_all(bind=engine)


class LocalDBStore:
    def __init__(self):
        self.session_factory = SessionLocal

    def login_player(self, username: str):
        db = self.session_factory()
        try:
            player = db.query(Player).filter(Player.username == username).first()
            if player is None:
                player = Player(username=username, score=0)
                db.add(player)
                db.commit()
                db.refresh(player)

            return {
                "id": player.id,
                "username": player.username,
                "score": player.score,
                "offline": True,
            }
        finally:
            db.close()

    def submit_answer(self, player_id: int, scenario_id: int, action_id: int):
        db = self.session_factory()
        try:
            player = db.query(Player).filter(Player.id == player_id).first()
            if player is None:
                return None

            action = (
                db.query(Action)
                .filter(
                    Action.id == action_id,
                    Action.scenario_id == scenario_id,
                )
                .first()
            )
            if action is None:
                return None

            already_played = (
                db.query(PlayerProgress)
                .filter(
                    PlayerProgress.player_id == player.id,
                    PlayerProgress.scenario_id == scenario_id,
                )
                .first()
            )
            if already_played:
                return {
                    "already_completed": True,
                    "message": "This scenario was already completed.",
                    "offline": True,
                }

            player.score += action.points_modifier
            if player.score < 0:
                player.score = 0

            progress = PlayerProgress(
                player_id=player.id,
                scenario_id=scenario_id,
                action_taken_id=action.id,
            )
            db.add(progress)
            db.commit()

            return {
                "status": "success",
                "new_score": player.score,
                "animal_message": action.animal_message,
                "is_correct": action.is_correct,
                "offline": True,
            }
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    def submit_arcade_score(self, player_id: int, level_number: int, score: int):
        db = self.session_factory()
        try:
            player = db.query(Player).filter(Player.id == player_id).first()
            if player is None:
                return None

            if not 1 <= level_number <= 4:
                return None

            if score < 0:
                return None

            arcade_score = (
                db.query(ArcadeScore)
                .filter(
                    ArcadeScore.player_id == player_id,
                    ArcadeScore.level_number == level_number,
                )
                .first()
            )

            points_added = 0

            if arcade_score is None:
                arcade_score = ArcadeScore(
                    player_id=player_id,
                    level_number=level_number,
                    best_score=score,
                )
                db.add(arcade_score)
                points_added = score
            elif score > arcade_score.best_score:
                points_added = score - arcade_score.best_score
                arcade_score.best_score = score

            player.score += points_added
            if player.score < 0:
                player.score = 0

            db.commit()
            db.refresh(player)
            db.refresh(arcade_score)

            return {
                "status": "success",
                "level_number": level_number,
                "submitted_score": score,
                "best_score": arcade_score.best_score,
                "points_added": points_added,
                "new_score": player.score,
                "offline": True,
            }
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()