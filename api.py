import os
from datetime import datetime
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey, DateTime, text, Table
from sqlalchemy.orm import declarative_base, sessionmaker, Session, relationship

# =====================================================================
# 1. СИГУРНОСТ И ПОВРЗУВАЊЕ СО БАЗА (.env)
# =====================================================================
load_dotenv()

# Доколку нема DATABASE_URL во .env, користиме локална Postgres база како резерва
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/game_db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# =====================================================================
# 2. SQLALCHEMY МОДЕЛИ (База на податоци)
# =====================================================================

# --- Сврзна табела за Many-to-Many релација меѓу SideHuman и Answer ---
side_human_answers = Table(
    "side_human_answers",
    Base.metadata,
    Column("side_human_id", Integer, ForeignKey("side_humans.id", ondelete="CASCADE"), primary_key=True),
    Column("answer_id", Integer, ForeignKey("right_answers.id", ondelete="CASCADE"), primary_key=True)
)


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


class SideHuman(Base):
    __tablename__ = "side_humans"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)

    # Релација со Answer преку сврзната табела
    solutions = relationship("Answer", secondary=side_human_answers, back_populates="side_humans")


class Answer(Base):
    __tablename__ = "right_answers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    description = Column(String)

    # Контра-релација
    side_humans = relationship("SideHuman", secondary=side_human_answers, back_populates="solutions")


# Автоматско креирање на сите табели во базата
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


class SideHumanCreate(BaseModel):
    name: str
    solutions: set[int]  # Клиентот праќа сет од ID-иња на одговори (на пр. [1, 2])


class AnswerCreate(BaseModel):
    name: str
    description: str


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

# Автоматски се извршува при секое палење или reload на API-то
@app.on_event("startup")
def auto_seed_on_startup():
    db = SessionLocal()
    try:
        # Ја повикуваме веќе постоечката функција за седување
        seed_database(db)
        print("🌱 Базата е автоматски освежена со најновиот SQL фајл!")
    except Exception as e:
        print(f"Грешка при автоматско освежување на базата: {e}")
    finally:
        db.close()

# --- ПОЛНЕЊЕ НА БАЗАТА (SEED) ---
@app.post("/seed/")
def seed_database(db: Session = Depends(get_db)):
    """
    Го чита seed_data.sql фајлот и ја полни базата со почетни прашања и одговори.
    """
    # Спречуваме дуплирање на податоци
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

    # 4. Ажурирање на поените на играчот
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


# --- ОДГОВОРИ (ANSWERS) ---
@app.post("/answers/")
def create_answer(answer: AnswerCreate, db: Session = Depends(get_db)):
    db_answer = db.query(Answer).filter(Answer.name == answer.name).first()
    if db_answer:
        raise HTTPException(status_code=400, detail="Answer already created")

    new_answer = Answer(name=answer.name, description=answer.description)
    db.add(new_answer)
    db.commit()
    db.refresh(new_answer)
    return new_answer


@app.get("/answers/{answer_id}")
def read_answer(answer_id: int, db: Session = Depends(get_db)):
    answer = db.query(Answer).filter(Answer.id == answer_id).first()
    if answer is None:
        raise HTTPException(status_code=404, detail="Answer not found")
    return answer


# --- СПРЕДНИ ЛИКОВИ (SIDE HUMANS) ---
@app.post("/side_humans/")
def create_side_human(side_human: SideHumanCreate, db: Session = Depends(get_db)):
    db_side_human = db.query(SideHuman).filter(SideHuman.name == side_human.name).first()
    if db_side_human:
        raise HTTPException(status_code=400, detail="Side Human already created")

    # Наоѓање на вистинските Answer објекти во базата
    db_answers = db.query(Answer).filter(Answer.id.in_(side_human.solutions)).all()

    if len(db_answers) != len(side_human.solutions):
        raise HTTPException(status_code=400, detail="One or more answer IDs do not exist in the database")

    new_side_human = SideHuman(name=side_human.name, solutions=db_answers)

    db.add(new_side_human)
    db.commit()
    db.refresh(new_side_human)
    return new_side_human


@app.get("/side_humans/{side_human_id}")
def read_side_human(side_human_id: int, db: Session = Depends(get_db)):
    side_human = db.query(SideHuman).filter(SideHuman.id == side_human_id).first()
    if side_human is None:
        raise HTTPException(status_code=404, detail="Side Human not found")
    return side_human


# --- РЕСЕТИРАЊЕ НА ПРОГРЕС ЗА НОВА ПАРТИЈА ---
@app.post("/players/{player_id}/reset/")
def reset_player_progress(player_id: int, db: Session = Depends(get_db)):
    """
    Го брише целиот прогрес во базата за овој играч и ги враќа неговите поени на 0,
    овозможувајќи му повторно да ја игра играта.
    """
    player = db.query(Player).filter(Player.id == player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Играчот не е пронајден")

    # 1. Го бришеме запишаниот прогрес за ова ID во базата
    db.query(PlayerProgress).filter(PlayerProgress.player_id == player_id).delete()

    # 2. Му ги ресетираме поените на 0 за новата партија
    player.score = 0
    db.commit()

    return {"status": "success", "message": "Прогресот и поените се успешно ресетирани!"}