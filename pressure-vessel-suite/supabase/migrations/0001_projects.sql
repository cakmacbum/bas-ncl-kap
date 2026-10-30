-- Kalıcı proje deposu. Erişim yalnız sunucudan servis anahtarıyla (RLS açık, politika yok:
-- anon/authenticated roller hiçbir satıra erişemez; service_role RLS'i atlar).
create table if not exists public.projects (
  id          text primary key,
  owner       text not null,
  data        jsonb not null,
  revision    integer not null default 1,
  updated_at  timestamptz not null default now()
);
create index if not exists projects_owner_idx on public.projects (owner, updated_at desc);

create table if not exists public.project_revisions (
  project_id  text not null references public.projects (id) on delete cascade,
  revision    integer not null,
  data        jsonb not null,
  created_at  timestamptz not null default now(),
  primary key (project_id, revision)
);

alter table public.projects enable row level security;
alter table public.project_revisions enable row level security;
