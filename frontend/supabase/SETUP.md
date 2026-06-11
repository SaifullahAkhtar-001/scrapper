# Supabase Setup

## 1. Run the SQL migration

1. Open Supabase Dashboard
2. Go to **SQL** (left sidebar)
3. Click **New query**
4. Copy the entire contents of `schema.sql` and paste into the editor
5. Click **Run**

Do NOT paste setup instructions from chat — only paste the SQL from `schema.sql`.

## 2. Enable email auth (in the Dashboard UI, not SQL)

1. Go to **Authentication** → **Providers**
2. Enable **Email**

## 3. Create a user

1. Go to **Authentication** → **Users**
2. Click **Add user**
3. Set email and password

## 4. Fetch is_scraper_running via API

```
GET https://YOUR_PROJECT.supabase.co/rest/v1/app_settings?key=eq.is_scraper_running&select=key,value,updated_at
```

Headers:
```
apikey: YOUR_ANON_KEY
Authorization: Bearer YOUR_ANON_KEY
```
