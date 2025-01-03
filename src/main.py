import sys
import controller


def main():
    controller.app.run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
else:
    raise Exception("don't import me, you idiot!")
