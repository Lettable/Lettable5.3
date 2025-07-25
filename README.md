A versatile Telegram bot framework built on Pyrogram, **LettableV5.1** runs multiple client sessions in parallel to handle user listings, vouches, referrals, credits, broadcasts, and full admin controls—ideal for username marketplaces and community management. It uses MongoDB for persistence, dynamic session loading for scalability, and fine‑grained access control via OWNER/SUDOERS.  

## 🚀 Features

Below is a complete command reference for LettableV5.1.

| Command      | Only Group | Used By  |
|--------------|------------|----------|
| `/start`     | false      | users    |
| `/source`    | false      | users    |
| `/list`      | false      | users    |
| `/cancel`    | false      | users    |
| `/block`     | false      | admins   |
| `/unblock`   | false      | admins   |
| `/blocked`   | false      | users    |
| `/broadcast` | false      | admins   |
| `/credit`    | false      | admins   |
| `/e`         | false      | admins   |
| `/sh`        | false      | admins   |
| `/refers`    | false      | users    |
| `/reset`     | false      | admins   |
| `/save`      | true       | admins   |
| `/state`     | false      | users    |
| `/invite`    | true       | admins   |
| `/addsudo`   | false      | admins   |
| `/delsudo`   | false      | admins   |
| `/sudolist`  | false      | users    |
| `/profile`   | false      | admins   |
| `/stats`     | false      | users    |

---

All other major features—dynamic multi‑client setup, listing workflows, vouch counters, credit tracking, referrals, and the developer console—are implemented under the hood as shown above. Feel free to scroll down for detailed descriptions of each module and configuration instructions.

> **Note:** `SUDOERS` in [`config.py`](./config.py) are _not_ the same as the “sudo users” stored in the database. Think of **sudo users** as your paying customers, and **SUDOERS** as the select circle of friends who always expect everything for free.

## 📦 Installation & Setup  
1. **Clone the repo**  
   ```bash
   git clone https://github.com/Lettable/LettableV5.1.git
   cd LettableV5.1
   ```

2. **Install requirements**  
   ```bash
   pip install -r requirements.txt
   ```

3. **Open [`config.py`](./config.py)** and configure your environment:  
   - All settings are documented inline—just update the variables to match your setup. :contentReference[oaicite:0]{index=0}  
   - Use relative links like [`config.py`](./config.py) for quick navigation. :contentReference[oaicite:1]{index=1}  
   - No further edits are required beyond what’s specified in the file. :contentReference[oaicite:2]{index=2}  

4. **Run**  
   ```bash
   bash start
   ```

## ⚙️ Configuration Variables  
| Variable              | Description                                                                                       |
|-----------------------|---------------------------------------------------------------------------------------------------|
| `OWNER`               | Single user ID with full control                                                                  |
| `SUDOERS`             | Space‑separated IDs of additional superusers (use only if `MAKE_SUDO_RICH = True`)                |
| `MAKE_SUDO_RICH`      | Toggle OWNER‑only (`False`) or OWNER + SUDOERS (`True`)                                            |
| `SESSION2`…`SESSION6` | String‑session keys for assistant clients; leave blank to skip                                   |
| `GROUP_ID`            | Main group for startup logs                                                                       |
| `VOUCH_CHANNEL_ID`    | Channel ID where forwarded messages increment vouch count                                         |
| `BROADCAST_CHANNEL_ID`| Channel ID where forwarded messages increment broadcast count                                     |
| `MARKETPLACE_ID`      | Forum chat ID for `/list` ads                                                                      |
| `TIME_DIFF`           | Delay (seconds) between automated messages to avoid rate limits                                    |
| `MONGO_DB_URI`        | MongoDB connection string                                                                         |
| `START_IMG`, `SOURCE_IMG` | URLs for `/start`, `/source` splash images                                                   |

## 🔖 Commands & Usage  

### General  
| Command     | Scope   | Description                                                                     |
|-------------|---------|---------------------------------------------------------------------------------|
| `/start`    | Private | Greet user and show main menu (from `app.py`)                                   |
| `/help`     | Private | Show help text and available commands                                           |

### Listing System (promo/modules/list.py)  
| Command       | Scope   | Description                                                                                                      |
|---------------|---------|------------------------------------------------------------------------------------------------------------------|
| `/list`       | Private | Begin interactive flow to select platform (Discord, Instagram…) and submit a username + price + additional info |
| `/cancel`     | Private | Cancel the current `/list` workflow                                                                               |

### User Management  
| Command      | Scope        | Description                                                          |
|--------------|--------------|----------------------------------------------------------------------|
| `/block`     | OWNER/SUDO   | Block a user by reply or ID/username citeturn6view0   |
| `/unblock`   | OWNER/SUDO   | Unblock a previously blocked user citeturn6view0 |
| `/blocked`   | Any          | List all blocked users                                               |
| `/addsudo`   | OWNER/SUDO   | Grant sudo privileges to a user citeturn8view0    |
| `/delsudo`   | OWNER/SUDO   | Revoke sudo privileges citeturn8view0    |
| `/sudolist`  | Any          | Display current sudo users citeturn8view0    |

### Broadcast & Vouch  
| Command         | Scope      | Description                                                                                     |
|-----------------|------------|-------------------------------------------------------------------------------------------------|
| `/broadcast`    | OWNER/SUDO | Forward a replied message to all stored users (1× per user) citeturn7view0             |
| _Auto vouch_    | Channel    | Count forwarded messages in `VOUCH_CHANNEL_ID` and edit its post citeturn9view0          |

### Credits & Stats  
| Command   | Scope        | Description                                                                             |
|-----------|--------------|-----------------------------------------------------------------------------------------|
| `/credit` | Any/SUDO     | Show target user’s credit balance + reset timer citeturn10view0      |
| `/stats`  | Any          | Show bot statistics (users, messages processed, etc.)                                   |

### Referral & Misc  
| Command  | Scope  | Description                                                            |
|----------|--------|------------------------------------------------------------------------|
| `/refers`| Any    | Generate or redeem referral codes (promo/modules/ref.py)               |
| `/save`  | Any    | Save current user state/data (promo/modules/save.py)                   |
| `/reset` | Any    | Clear saved state/data (promo/modules/reset.py)                        |
| `/dev`   | OWNER  | Execute Python code snippets on the server                             |

## 🤝 Contributing  
1. Fork the repo  
2. Create a feature branch (`git checkout -b feature/foo`)  
3. Commit your changes with conventional messages (`feat: …`, `fix: …`)  
4. Open a Pull Request and explain your improvements  

📬 Join our Telegram channel for updates and support: [@mizryave](https://t.me/mizryave)  

💖 Donations are greatly appreciated!  
If you’d like to help fund ongoing development, feel free to contribute:  
- [Telegram](https://t.me/mirzyave)  
