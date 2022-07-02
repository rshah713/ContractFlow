# ContractFlow
An iOS App to manage workflow for contractors.

### Technologies

- Built in Python with [kivy](https://github.com/kivy/kivy)
- Deployed and packaged with [toolchain](https://github.com/kivy/kivy-ios)
- Backend with [Firebase REST API](https://firebase.google.com)

### Usage

To run the app from the Python interpreter:
```bash
python3 main.py
```
To run from the Xcode Simulator:

1. Install dependencies (using brew and Xcode 10+)

```
xcode-select --install
brew install autoconf automake libtool pkg-config
brew link libtool
```

2. Start compilation

```
toolchain build python3 kivy
```

3. Create the Xcode Project
```
toolchain create ContractFlow ~/user/Desktop/ContractFlow/xcode
open contractflow-ios/contractflow.xcodeproj
```

4. Click `Play` within Xcode
