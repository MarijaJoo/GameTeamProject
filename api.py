from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String, Table, ForeignKey
from sqlalchemy.orm import sessionmaker, Session, relationship, declarative_base
from pydantic import BaseModel

# 1. Подесување на конекцијата
DATABASE_URL = "postgresql://user:password@localhost/game_db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- 2. Сврзна табела за Many-to-Many релација ---
# Оваа табела служи како мост меѓу SideHuman и Answer
side_human_answers = Table(
    "side_human_answers",
    Base.metadata,
    Column("side_human_id", Integer, ForeignKey("side_humans.id", ondelete="CASCADE"), primary_key=True),
    Column("answer_id", Integer, ForeignKey("right_answers.id", ondelete="CASCADE"), primary_key=True)
)


# --- 3. SQLAlchemy Модели (База) ---

class Player(Base):
    __tablename__ = "players"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    score = Column(Integer, default=0)


class SideHuman(Base):
    __tablename__ = "side_humans"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)

    # Релација со Answer преку свзната табела
    solutions = relationship("Answer", secondary=side_human_answers, back_populates="side_humans")


class Answer(Base):
    __tablename__ = "right_answers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    description = Column(String)

    # Контра-релација (опционално, но корисно ако сакаш да знаеш кој Human го има овој одговор)
    side_humans = relationship("SideHuman", secondary=side_human_answers, back_populates="solutions")


# Креирање на сите табели одеднаш
Base.metadata.create_all(bind=engine)


# --- 4. Pydantic Модели (DTO) ---

class PlayerCreate(BaseModel):
    username: str
    score: int


class SideHumanCreate(BaseModel):
    name: str
    solutions: set[int]  # Клиентот сè уште праќа сет од ID-иња (на пр. [1, 2])


class AnswerCreate(BaseModel):
    name: str
    description: str


# --- 5. Иницијализација на FastAPI ---

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- 6. REST Ендпоинти ---

# --- PLAYERS ---
@app.post("/players/")
def create_player(player: PlayerCreate, db: Session = Depends(get_db)):
    db_player = db.query(Player).filter(Player.username == player.username).first()
    if db_player:
        raise HTTPException(status_code=400, detail="Username already registered")

    new_player = Player(username=player.username, score=player.score)
    db.add(new_player)
    db.commit()
    db.refresh(new_player)
    return new_player


@app.get("/players/{player_id}")
def read_player(player_id: int, db: Session = Depends(get_db)):
    player = db.query(Player).filter(Player.id == player_id).first()
    if player is None:
        raise HTTPException(status_code=404, detail="Player not found")
    return player


# --- ANSWERS ---
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


# --- SIDE HUMANS ---
@app.post("/side_humans/")
def create_side_human(side_human: SideHumanCreate, db: Session = Depends(get_db)):
    db_side_human = db.query(SideHuman).filter(SideHuman.name == side_human.name).first()
    if db_side_human:
        raise HTTPException(status_code=400, detail="Side Human already created")

    # 1. Ги наоѓаме вистинските Answer објекти во базата според испратените ID-иња
    db_answers = db.query(Answer).filter(Answer.id.in_(side_human.solutions)).all()

    # Валидација: Дали сите пратени ID-иња навистина постојат во базата?
    if len(db_answers) != len(side_human.solutions):
        raise HTTPException(status_code=400, detail="One or more answer IDs do not exist in the database")

    # 2. Го креираме SideHuman и му ги доделуваме пронајдените Answer објекти во релацијата
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