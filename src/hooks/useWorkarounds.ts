import { useState, useEffect, useCallback } from "react";
import { toaster } from "@decky/api";
import { getWorkarounds, setWorkaround } from "../api/omfgApi";

export interface WorkaroundState {
  mesa_immediate: boolean;
  disable_vkbasalt: boolean;
}

export function useWorkarounds() {
  const [workarounds, setWorkarounds] = useState<WorkaroundState>({
    mesa_immediate: false,
    disable_vkbasalt: false,
  });

  const fetchWorkarounds = useCallback(async () => {
    try {
      const result = await getWorkarounds();
      if (result.success) {
        setWorkarounds({
          mesa_immediate: result.mesa_immediate,
          disable_vkbasalt: result.disable_vkbasalt,
        });
      }
    } catch { /* keep defaults */ }
  }, []);

  const toggle = useCallback(async (key: keyof WorkaroundState, enabled: boolean) => {
    try {
      const result = await setWorkaround(key, enabled);
      if (result.success) {
        setWorkarounds((prev) => ({ ...prev, [key]: enabled }));
      } else {
        toaster.toast({ title: "Workaround failed", body: result.error ?? "Unknown error" });
      }
    } catch (e) {
      toaster.toast({ title: "Workaround failed", body: String(e) });
    }
  }, []);

  useEffect(() => { fetchWorkarounds(); }, [fetchWorkarounds]);

  return { workarounds, toggle };
}
