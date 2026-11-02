import { getCurrentUser } from "./api";

export async function hasSession(): Promise<boolean> {
  return getCurrentUser();
}
