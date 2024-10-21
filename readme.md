# PiShock SB (Discord Self-Bot)

**PiShock SB** is a Discord selfbot that allows you (or others) to shock your account using [PiShock](https://pishock.com/).

allows for custom words triggers for shocking such as `(word) (shock value) (duration)`

miscellaneous features:

- status <type> <status> (type: 1 - Game, 2 - Streaming, 3 - Listening, 4 - Watching)
- avatar <user>
- banner <user>

> ### ⚠️ **Warning:** Selfbots are against Discord's TOS but bans are likely unless you spam Discord's API or openly show it in public discord servers. I am not responsible for any issues/bans.

## Step 1: Clone the Repository

open your cmd/terminal of choice and run the following command

`git clone https://github.com/blahjar/pi-sb`

This will clone the repository to your machine.

## Step 2: Navigate to the Repository Folder

Once the repo is cloned, navigate into the project folder:

`cd pi-sb` or `mvdir

This will change the current directory to the `pi-sb` folder, where the files are located.

## Step 3: Virtual Environment

> ### ⚠️ It's recommended to use a virtual environment but can be skipped if you really want, and skip step 3 and go onto 4

> ⚠️ **Warning:** if discord requirement is already installed you need to uninstall discord and install discord.py-self if no virtual env.

### Windows

1. Open CMD and navigate to the project directory.
2. Run the following command to create a virtual environment:

   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:

   ```bash
   .\venv\Scripts\activate
   ```

4. Now you're in the virtual environment. Install the required dependencies by running:

   ```bash
   pip install -r requirements.txt
   ```

### Linux

1. Open your terminal and navigate to the project directory.
2. Run the following command to create a virtual environment:

   ```bash
   python3 -m venv venv
   ```

3. Activate the virtual environment:

   ```bash
   source venv/bin/activate
   ```

4. Now you're in the virtual environment. Install the required dependencies by running:

   ```bash
   pip install -r requirements.txt
   ```

## Step 4: Get the Required API Key and Configurations

To proceed, you will need the following credentials from [PiShock](https://pishock.com):

1. **API Key**:
   - The API Key is generated on the PiShock website and can be found in the **Account** section of your account dashboard.
2. **Sharecode**:
   - The Sharecode is a unique code generated on PiShock.com for your device.
3. **Username**:
   - The **Username** is the one you use to log into PiShock.com. You can find it in the **Account** section of your dashboard.

---

### Getting Your Discord Token

1. Open **Discord** in your web browser (preferably in **Developer Tools**).
2. Press **Ctrl + Shift + I**.

3. Navigate to the **Console** tab.

4. Paste the following code into the console and hit **Enter**:

   ```javascript
   (webpackChunkdiscord_app.push([
     [""],
     {},
     (e) => {
       m = [];
       for (let c in e.c) m.push(e.c[c]);
     },
   ]),
   m)
     .find((m) => m?.exports?.default?.getToken !== void 0)
     .exports.default.getToken();
   ```

## Step 5: Start the selfbot

Once everything is installed, run `cp example.env .env` or manually rename the example.env
and then you can run the selfbot using the following command:

`python gui.py` - starts the gui for the selfbot
configure everything in the gui or manually in the .env
