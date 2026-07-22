def main() -> int:
    try:

        print(f"Hello from {__name__}")
        return 0

    except Exception as e:
        print(f"Exception thrown: {e}")
        raise Exception(e)


if __name__ == "__main__":
    main()
