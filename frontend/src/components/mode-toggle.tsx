import { Moon, Sun } from "lucide-react"

import { useTheme } from "@/components/provider/theme-provider"
import { Button } from "./ui/button"

export function ModeToggle() {
  const { theme, setTheme } = useTheme()

  const toggleTheme = () => {
    setTheme(theme === "dark" ? "light" : "dark")
  }

  return (
     <Button
      variant="outline"
      size="icon"
      onClick={toggleTheme}
      className="
        rounded-full
        bg-light-grey
        border-ui
        text-text-1
        hover:bg-white
        dark:bg-dark
        dark:text-text-1-dark
        dark:hover:bg-dark-2
        dark:border-ui
        relative
      "
    >
      <Sun className="h-4 w-4 scale-100 rotate-0 transition-all dark:scale-0 dark:-rotate-90" />
      <Moon className="absolute h-4 w-4 scale-0 rotate-90 transition-all dark:scale-100 dark:rotate-0" />
      <span className="sr-only">Toggle theme</span>
    </Button>
  )
}