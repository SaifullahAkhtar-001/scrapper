create table if not exists public.app_settings (
  key text primary key,
  value jsonb not null default 'false'::jsonb,
  is_public boolean not null default false,
  description text,
  updated_at timestamptz not null default now()
);

insert into public.app_settings (key, value, is_public, description)
values
  ('is_scraper_running', 'false'::jsonb, true, 'Whether the scraper process is currently active'),
  ('scraper_last_run_at', 'null'::jsonb, true, 'ISO timestamp of last scraper run')
on conflict (key) do nothing;

create or replace function public.set_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

drop trigger if exists app_settings_updated_at on public.app_settings;
create trigger app_settings_updated_at
  before update on public.app_settings
  for each row execute function public.set_updated_at();

alter table public.app_settings enable row level security;

drop policy if exists "Authenticated users can read all settings" on public.app_settings;
create policy "Authenticated users can read all settings"
  on public.app_settings for select
  to authenticated
  using (true);

drop policy if exists "Authenticated users can insert settings" on public.app_settings;
create policy "Authenticated users can insert settings"
  on public.app_settings for insert
  to authenticated
  with check (true);

drop policy if exists "Authenticated users can update settings" on public.app_settings;
create policy "Authenticated users can update settings"
  on public.app_settings for update
  to authenticated
  using (true)
  with check (true);

drop policy if exists "Authenticated users can delete settings" on public.app_settings;
create policy "Authenticated users can delete settings"
  on public.app_settings for delete
  to authenticated
  using (true);

drop policy if exists "Public can read public settings" on public.app_settings;
create policy "Public can read public settings"
  on public.app_settings for select
  to anon
  using (is_public = true);

create table if not exists public.profiles (
  id uuid primary key references auth.users (id) on delete cascade,
  email text,
  created_at timestamptz not null default now()
);

alter table public.profiles enable row level security;

drop policy if exists "Users can read own profile" on public.profiles;
create policy "Users can read own profile"
  on public.profiles for select
  to authenticated
  using (auth.uid() = id);

drop policy if exists "Users can update own profile" on public.profiles;
create policy "Users can update own profile"
  on public.profiles for update
  to authenticated
  using (auth.uid() = id);

create or replace function public.handle_new_user()
returns trigger
language plpgsql
security definer set search_path = public
as $$
begin
  insert into public.profiles (id, email)
  values (new.id, new.email)
  on conflict (id) do nothing;
  return new;
end;
$$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute function public.handle_new_user();
