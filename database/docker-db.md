You can access your database in two ways: using the **Command Line** (quickest way to check data) or a **GUI Tool** (like pgAdmin or DBeaver, best for managing data).

Since your database is running inside a Docker container but mapped to port `5432` on your laptop, here is how to connect:

### Method 1: The Quickest Way (Command Line)

You can log directly into the database from your terminal without installing anything extra.

1. **Find your Database Container Name:**
Run this command to list running containers:
```bash
docker ps

```


Look for the container named something like `todo-app-db-1` or `todo-app-db`.
2. **Log in:**
Run this command (replace `todo-app-db-1` with your actual container name if different):
```bash
docker exec -it todo-app-db-1 psql -U todo_user -d todo_db

```


3. **Run SQL Queries:**
Once you see the prompt `todo_db=#`, you can type SQL commands:
* `\dt` (List all tables)
* `SELECT * FROM "users";` (See all registered users)
* `SELECT * FROM todo;` (See all tasks)
* `\q` (Quit/Exit)



---

### Method 2: The Visual Way (pgAdmin / DBeaver)

If you prefer clicking through tables, you can use a tool like **pgAdmin** or **DBeaver** installed on your Windows machine.

**Connection Details:**

* **Host Name / Address:** `localhost`
* **Port:** `5432`
* **Maintenance Database:** `todo_db`
* **Username:** `todo_user`
* **Password:** `Computer123`

**Why `localhost`?**
Even though the database is in a container, your `docker-compose.yml` file has the line `ports: - "5432:5432"`. This "forwards" the container's port to your laptop's localhost, allowing external tools to connect to it.

---

### ⚠️ Troubleshooting

If you cannot connect via `localhost`, ensure your `docker-compose.yml` has the port mapping correctly set for the `db` service:

```yaml
  db:
    image: postgres:13
    # ... environment variables ...
    ports:
      - "5432:5432"  <-- This line is required for Method 2 to work

```

That is fantastic news! 🎉

Changing the port to `5435` confirmed that you had a "phantom" Postgres server running on your main port. Now that you have a clean pipeline into your Docker container, here is how to use it.

### How to Run SQL Commands in pgAdmin

1. **Open the Query Tool:**
* In the left sidebar (Browser), click the **arrow** next to your server (`ProTodo Docker`).
* Click **Databases** > **todo_db**.
* **Right-click** on `todo_db` and select **Query Tool**.
* A blank white panel will open on the right side. This is your terminal for the database.


2. **Run a Test Command:**
* Type the following command into the white panel:
```sql
SELECT * FROM "user";

```


* **Note:** Remember to keep the double quotes `""` around `user` because it is a reserved word.
* Click the **Play Button** (▶️) in the toolbar above the text area (or press `F5`).


3. **View Results:**
* Look at the **Data Output** tab at the bottom. You should see the user you created (likely your own email) listed there.



### 💡 Useful DevOps Commands to Try

Since you are testing, try these commands to see your app's data structure:

* **See all Tasks:**
```sql
SELECT * FROM todo;

```


* **Check User Timezones (to verify your updates):**
```sql
SELECT id, email, timezone FROM "user";

```


* **Reset a Password Manually (Emergency DevOps Task):**
If a user forgets their password and email is broken, you can manually delete them so they can sign up again:
```sql
DELETE FROM "user" WHERE email = 'myemail@example.com';

```



---

### 🚀 Next Step: The Cloud (AWS S3)

Now that your **Local Environment** is perfect:

1. Container is running ✅
2. Email is sending ✅
3. Security (1-hour token) is active ✅
4. Database is accessible via GUI ✅

We are ready to move to **AWS S3** to fix the image storage issue.

**Please log in to your AWS Console**, search for **S3**, and let me know when you are there!