import { AuthProvider } from "@/contexts/AuthContext";
import { WebSocketProvider } from "@/contexts/WebSocketContext";
import { ThemeProvider } from "./theme-provider";
import type { ReactNode } from "react";

export default function RootProvider({children}: {children: ReactNode}) {
  return  <AuthProvider>
        <WebSocketProvider>
          <ThemeProvider defaultTheme='dark' storageKey='vite-ui-theme'>{children}</ThemeProvider>
                </WebSocketProvider>
              </AuthProvider>
}