"use client";

import { useEffect, useState } from "react";

/** True below ``px`` wide (phones). False on the server and in tests
 * unless matchMedia says so. */
export function useNarrow(px = 640) {
  const [narrow, setNarrow] = useState(false);
  useEffect(() => {
    if (typeof window === "undefined" || !window.matchMedia) return undefined;
    const query = window.matchMedia(`(max-width: ${px - 1}px)`);
    const update = () => setNarrow(query.matches);
    update();
    query.addEventListener?.("change", update);
    return () => query.removeEventListener?.("change", update);
  }, [px]);
  return narrow;
}
