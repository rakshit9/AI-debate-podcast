"use client";

import { useState, useEffect } from "react";
import type { ToastProps } from "@/components/ui/toast";

type ToastState = ToastProps & {
  id: string;
  title?: string;
  description?: string;
  open: boolean;
};

type Action =
  | { type: "ADD_TOAST"; toast: ToastState }
  | { type: "UPDATE_TOAST"; toast: Partial<ToastState> & { id: string } }
  | { type: "DISMISS_TOAST"; toastId?: string }
  | { type: "REMOVE_TOAST"; toastId?: string };

interface State {
  toasts: ToastState[];
}

let count = 0;
function genId() {
  count = (count + 1) % Number.MAX_SAFE_INTEGER;
  return count.toString();
}

const toastTimeouts = new Map<string, ReturnType<typeof setTimeout>>();

function reducer(state: State, action: Action): State {
  switch (action.type) {
    case "ADD_TOAST":
      return { ...state, toasts: [action.toast, ...state.toasts].slice(0, 5) };
    case "UPDATE_TOAST":
      return {
        ...state,
        toasts: state.toasts.map((t) => (t.id === action.toast.id ? { ...t, ...action.toast } : t)),
      };
    case "DISMISS_TOAST":
      return {
        ...state,
        toasts: state.toasts.map((t) =>
          t.id === action.toastId || !action.toastId ? { ...t, open: false } : t,
        ),
      };
    case "REMOVE_TOAST":
      if (!action.toastId) return { ...state, toasts: [] };
      return { ...state, toasts: state.toasts.filter((t) => t.id !== action.toastId) };
  }
}

const listeners: Array<(state: State) => void> = [];
let memoryState: State = { toasts: [] };

function dispatch(action: Action) {
  memoryState = reducer(memoryState, action);
  listeners.forEach((l) => l(memoryState));
}

function toast({
  title,
  description,
  variant,
  duration = 4000,
}: {
  title?: string;
  description?: string;
  variant?: "default" | "destructive";
  duration?: number;
}) {
  const id = genId();
  const dismiss = () => dispatch({ type: "DISMISS_TOAST", toastId: id });

  dispatch({
    type: "ADD_TOAST",
    toast: { id, title, description, variant, open: true, onOpenChange: (open) => { if (!open) dismiss(); } },
  });

  const timeout = setTimeout(dismiss, duration);
  toastTimeouts.set(id, timeout);

  return { id, dismiss };
}

function useToast() {
  const [state, setState] = useState<State>(memoryState);

  useEffect(() => {
    listeners.push(setState);
    return () => {
      const idx = listeners.indexOf(setState);
      if (idx > -1) listeners.splice(idx, 1);
    };
  }, []);

  return {
    ...state,
    toast,
    dismiss: (toastId?: string) => dispatch({ type: "DISMISS_TOAST", toastId }),
  };
}

export { useToast, toast };
