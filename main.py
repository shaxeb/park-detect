import subprocess

def switch_program():
    """Switches between camera_setup.py and detect.py based on user input"""
    while True:
        print("Select an option:")
        print("1. Run camera_setup.py")
        print("2. Run detect.py")
        print("3. Exit")

        choice = input("Enter your choice (1-3): ")

        if choice == "1":
            subprocess.call(["python", "camera_setup.py"])
        elif choice == "2":
            subprocess.call(["python", "detect.py"])
        elif choice == "3":
            break
        else:
            print("Invalid choice. Please try again.")

switch_program()
