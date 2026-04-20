from app.database import engine
from app.models import Base


def main():
    print("Creating tables")
    Base.metadata.create_all(bind=engine)
    print("done")


if __name__ == "__main__":
    main()