# ContractFlow
An iOS App to manage workflow for contractors.

> ContractFlow is live on the [App Store](https://apps.apple.com/us/app/contractflow/id1637464399).

<img src="https://is3-ssl.mzstatic.com/image/thumb/PurpleSource122/v4/aa/ab/12/aaab12dc-154e-0dc3-c415-2ba5fb4451d2/58842b1d-facb-4584-892d-7f2f15577d8e_Simulator_Screen_Shot_-_iPhone_11_Pro_Max_-_2022-08-11_at_18.45.32.png/300x0w.webp" alt="login screen" width="100"/>  <img src="https://is2-ssl.mzstatic.com/image/thumb/PurpleSource122/v4/ef/19/08/ef19084f-31dc-16aa-ba25-d4802d17c8b8/3a6c176d-559b-4e34-9bc7-4395c5eafc82_Simulator_Screen_Shot_-_iPhone_11_Pro_Max_-_2022-08-11_at_18.46.30.png/300x0w.webp" alt="dashboard screen" width="100"/>  <img src="https://is1-ssl.mzstatic.com/image/thumb/PurpleSource112/v4/df/a1/27/dfa127f7-7be4-4ba3-46b3-48fccce67aab/de12210e-2be4-4c21-a571-0cb29e66953c_Simulator_Screen_Shot_-_iPhone_11_Pro_Max_-_2022-08-11_at_18.46.42.png/300x0w.webp" alt="locations screen" width="100"/>  <img src="https://is4-ssl.mzstatic.com/image/thumb/PurpleSource112/v4/be/77/70/be77704b-facc-d6ee-bdc6-fdf0a1181020/b1935a40-e6b5-4851-a8dd-f3f4a8bb3138_Simulator_Screen_Shot_-_iPhone_11_Pro_Max_-_2022-08-11_at_18.47.20.png/300x0w.webp" alt="meeting screen" width="100"/>  <img src="https://is5-ssl.mzstatic.com/image/thumb/PurpleSource112/v4/42/23/44/4223441e-552c-15ea-ef18-61973696a22f/57723b2c-33cc-43d3-9702-a27c1320b57d_Simulator_Screen_Shot_-_iPhone_11_Pro_Max_-_2022-08-11_at_18.53.41.png/300x0w.webp" alt="settings screen" width="100"/>





### Technologies

- Built in Python with [kivy](https://github.com/kivy/kivy)
- Deployed and packaged with [toolchain](https://github.com/kivy/kivy-ios)
- Backend with [Firebase REST API](https://firebase.google.com)

### Run Locally
1. Clone the repo
2. Create a folder in `ContractFlow` called `authentication`
3. Create `auth.py` in `authentication`
4. Store your Firebase Web API Key in a constant called `API_KEY`
    - Project Settings --> General --> Web API Key
5. Store your Firebase Project URL in a constant called `BASE_URL`
    - "https://<your-project-name>-default-rtdb.firebaseio.com/"
6. Install Kivy-Garden dependencies
    ```
    garden install circularlayout
    garden install circulardatetimepicker
    ```
    - If you get `zsh: command not found: garden`, please [install kivy-garden](https://kivy-garden.github.io/#legacygardentoolgeneralusageguidelines)
    
7. Follow the steps in Usage


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

3. Create the Xcode Project (where the directory is your source code)
```
toolchain create ContractFlow ~/user/Desktop/ContractFlow
open contractflow-ios/contractflow.xcodeproj
```

4. Click `Play` within Xcode
