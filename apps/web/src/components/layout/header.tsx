"use client";

import { useRouter } from "next/navigation";
import { LogOut } from "lucide-react";
import { Button } from "@/components/ui/button";
import { clearTokens } from "@/lib/auth";

interface HeaderProps {
  title: string;
}

export function Header({ title }: HeaderProps) {
  const router = useRouter();

  function handleLogout() {
    clearTokens();
    router.push("/login");
  }

  return (
    <header className="flex h-14 items-center justify-between border-b bg-card px-6">
      <h1 className="font-semibold text-lg">{title}</h1>
      <Button variant="ghost" size="sm" onClick={handleLogout}>
        <LogOut className="h-4 w-4 mr-2" />
        Logout
      </Button>
    </header>
  );
}
