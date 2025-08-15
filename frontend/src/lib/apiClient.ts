"use client";

import { getAuth } from "firebase/auth";

const RAW_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";
const API_BASE = RAW_BASE.replace(/\/+$/, ""); 
const API_PREFIX = "/api/v1";

function buildUrl(path: string) {
  const p = path.startsWith("/") ? path : `/${path}`;
  return `${API_BASE}${API_PREFIX}${p}`;
}

async function getIdToken(): Promise<string> {
  const auth = getAuth();
  const user = auth.currentUser;
  if (!user) throw new Error("未ログインのためAPIを呼び出せません。");
  return user.getIdToken(true);
}

async function handle<T>(res: Response, label: string): Promise<T> {
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`${label} failed: ${res.status} ${text}`);
  }
  return res.json() as Promise<T>;
}

export async function apiGet<T>(path: string, init?: RequestInit): Promise<T> {
  const token = await getIdToken();
  const url = buildUrl(path);
  // console.debug("[api:get]", url);
  const res = await fetch(url, {
    ...init,
    method: "GET",
    headers: {
      ...(init?.headers || {}),
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    cache: "no-store",
  });
  return handle<T>(res, `GET ${path}`);
}

export async function apiPut<T>(path: string, body: unknown, init?: RequestInit): Promise<T> {
  const token = await getIdToken();
  const url = buildUrl(path);
  // console.debug("[api:put]", url, body);
  const res = await fetch(url, {
    ...init,
    method: "PUT",
    headers: {
      ...(init?.headers || {}),
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(body ?? {}),
  });
  return handle<T>(res, `PUT ${path}`);
}

export async function apiPost<T>(path: string, body: unknown, init?: RequestInit): Promise<T> {
  const token = await getIdToken();
  const url = buildUrl(path);
  // console.debug("[api:post]", url, body);
  const res = await fetch(url, {
    ...init,
    method: "POST",
    headers: {
      ...(init?.headers || {}),
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(body ?? {}),
  });
  return handle<T>(res, `POST ${path}`);
}
