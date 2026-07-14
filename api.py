import os
from datetime import datetime
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey, DateTime, text
from sqlalchemy.orm import declarative_base, sessionmaker, Session, relationship

# =====================================================================
# 1. СИГУРНОСТ И ПОВРЗУВАЊЕ СО БАЗА (.env)
# =====================================================================
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL is None:
    raise ValueError("Грешка: DATABASE_URL не е пронајден во твојот .env фајл!")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# =====================================================================
# 2. SQLALCHEMY МОДЕЛИ (База на податоци)
# =====================================================================

class Player(Base):
    __tablename__ = "players"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    score = Column(Integer, default=0)

    # Релација кон табелата за прогрес
    progress = relationship("PlayerProgress", back_populates="player")


class Scenario(Base):
    __tablename__ = "scenarios"
    id = Column(Integer, primary_key=True, index=True)
    npc_name = Column(String)
    description = Column(String)

    # Едно сценарио содржи повеќе можни акции
    actions = relationship("Action", back_populates="scenario", cascade="all, delete-orphan")


class Action(Base):
    __tablename__ = "actions"
    id = Column(Integer, primary_key=True, index=True)
    scenario_id = Column(Integer, ForeignKey("scenarios.id"))

    action_text = Column(String)
    is_correct = Column(Boolean)
    points_modifier = Column(Integer)
    animal_message = Column(String)  # Пораката што ја изговара животинчето за овој избор

    scenario = relationship("Scenario", back_populates="actions")


class PlayerProgress(Base):
    __tablename__ = "player_progress"
    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"))
    scenario_id = Column(Integer, ForeignKey("scenarios.id"))
    action_taken_id = Column(Integer, ForeignKey("actions.id"))
    completed_at = Column(DateTime, default=datetime.utcnow)

    player = relationship("Player", back_populates="progress")
    scenario = relationship("Scenario")
    action = relationship("Action")


# Автоматско креирање на сите табели во PostgreSQL
Base.metadata.create_all(bind=engine)


# =====================================================================
# 3. PYDANTIC ШЕМИ / DTOs (Валидација на податоци)
# =====================================================================

class PlayerCreate(BaseModel):
    username: str
    score: int = 0


class ActionResponse(BaseModel):
    id: int
    action_text: str
    is_correct: bool
    points_modifier: int
    animal_message: str

    class Config:
        from_attributes = True


class ScenarioResponse(BaseModel):
    id: int
    npc_name: str
    description: str
    actions: list[ActionResponse]

    class Config:
        from_attributes = True


class ProgressCreate(BaseModel):
    player_id: int
    scenario_id: int
    action_id: int


# =====================================================================
# 4. ИНИЦИЈАЛИЗАЦИЈА НА FASTAPI И DEPENDENCY
# =====================================================================
app = FastAPI(title="Cyber Security Game API")


# Dependency за добивање сесија од базата
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =====================================================================
# 5. REST ЕНДПОИНТИ
# =====================================================================

# --- ПОЛНЕЊЕ НА БАЗАТА (SEED) ---
@app.post("/seed/")
def seed_database(db: Session = Depends(get_db)):
    """
    Го чита seed_data.sql фајлот и ја полни базата со почетни прашања и одговори.
    """
    # Спречуваме дуплирање на податоци ако веќе има нешто во базата
    if db.query(Scenario).first() is not None:
        return {"message": "Базата веќе содржи податоци. Нема потреба од седување."}

    seed_file_path = os.path.join(os.path.dirname(__file__), "seed_data.sql")

    if not os.path.exists(seed_file_path):
        raise HTTPException(status_code=404, detail="Фајлот seed_data.sql не е пронајден во фолдерот!")

    try:
        with open(seed_file_path, "r", encoding="utf-8") as file:
            sql_script = file.read()
            db.execute(text(sql_script))
            db.commit()
            return {"message": "Успешно внесени податоците од seed_data.sql!"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Грешка при извршување на скриптата: {str(e)}")


# --- ИГРАЧИ (PLAYERS) ---
@app.post("/players/")
def create_player(player: PlayerCreate, db: Session = Depends(get_db)):
    db_player = db.query(Player).filter(Player.username == player.username).first()
    if db_player:
        return db_player  # Ако постои играчот, само го враќаме за да се логира

    new_player = Player(username=player.username, score=player.score)
    db.add(new_player)
    db.commit()
    db.refresh(new_player)
    return new_player


@app.get("/players/{player_id}")
def read_player(player_id: int, db: Session = Depends(get_db)):
    player = db.query(Player).filter(Player.id == player_id).first()
    if player is None:
        raise HTTPException(status_code=404, detail="Играчот не е пронајден")
    return player


# --- СЦЕНАРИЈА И АКЦИИ (SCENARIOS & ACTIONS) ---
@app.get("/scenarios/", response_model=list[ScenarioResponse])
def get_all_scenarios(db: Session = Depends(get_db)):
    """
    Враќа листа на сите сценарија заедно со нивните можни акции (одговори).
    """
    return db.query(Scenario).all()


@app.get("/scenarios/{scenario_id}", response_model=ScenarioResponse)
def get_scenario(scenario_id: int, db: Session = Depends(get_db)):
    """
    Враќа едно конкретно сценарио со неговите можни акции.
    """
    scenario = db.query(Scenario).filter(Scenario.id == scenario_id).first()
    if scenario is None:
        raise HTTPException(status_code=404, detail="Сценариото не е пронајдено")
    return scenario


# --- ПРОГРЕС И ЗАЧУВУВАЊЕ ПОЕНИ (PROGRESS) ---
@app.post("/progress/")
def save_progress(progress_data: ProgressCreate, db: Session = Depends(get_db)):
    """
    Го зачувува изборот на играчот, ги ажурира неговите поени во табелата `players`
    и го бележи чекорот во `player_progress`.
    """
    # 1. Проверка дали играчот постои
    player = db.query(Player).filter(Player.id == progress_data.player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Играчот не е пронајден")

    # 2. Проверка дали акцијата постои и дали му припаѓа на тоа сценарио
    action = db.query(Action).filter(
        Action.id == progress_data.action_id,
        Action.scenario_id == progress_data.scenario_id
    ).first()

    if not action:
        raise HTTPException(status_code=404, detail="Невалидна акција или сценарио")

    # 3. Проверка дали веќе е изиграно ова сценарио од овој играч
    already_played = db.query(PlayerProgress).filter(
        PlayerProgress.player_id == player.id,
        PlayerProgress.scenario_id == progress_data.scenario_id
    ).first()

    if already_played:
        raise HTTPException(status_code=400, detail="Ова сценарио веќе го имаш поминато!")

    # 4. Ажурирање на поените на играчот (може да бидат плус или минус)
    player.score += action.points_modifier
    if player.score < 0:
        player.score = 0  # Поените не можат да одат под нула

    # 5. Запишување во табелата за прогрес
    new_progress = PlayerProgress(
        player_id=player.id,
        scenario_id=progress_data.scenario_id,
        action_taken_id=action.id
    )

    db.add(new_progress)
    db.commit()

    return {
        "status": "success",
        "new_score": player.score,
        "animal_message": action.animal_message,
        "is_correct": action.is_correct
    }