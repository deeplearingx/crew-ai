import os
import sys

os.environ.setdefault("PYTHONIOENCODING", "utf-8")

from dotenv import load_dotenv
from dev_crew import DevCrew
from dev_crew.tools.logger import reset_timer, log_crew_start, log_crew_done


def main():
    load_dotenv()

    if len(sys.argv) < 2:
        print('Usage: python main.py "<your requirement>"')
        print('Example: python main.py "Create a FastAPI app with CRUD endpoints for a Todo model"')
        sys.exit(1)

    requirement = " ".join(sys.argv[1:])
    print(f"Starting DevCrew with requirement: {requirement}")
    print(f"Log file: logs/dev_crew.log (tail -f logs/dev_crew.log to watch)")
    print()

    reset_timer()
    log_crew_start(requirement)

    crew = DevCrew()
    result = crew.crew().kickoff(inputs={"requirement": requirement})

    log_crew_done()

    print("\n" + "=" * 60)
    print("FINAL RESULT")
    print("=" * 60)
    print(result.raw)

    return result


if __name__ == "__main__":
    main()
