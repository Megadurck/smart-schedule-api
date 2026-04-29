import * as React from "react"
import { CalendarDays } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { cn } from "@/lib/utils"

type BaseMaskedInputProps = Omit<React.ComponentProps<typeof Input>, "type" | "value" | "onChange"> & {
  value: string
  onValueChange: (value: string) => void
}

function onlyDigits(value: string) {
  return value.replace(/\D/g, "")
}

function formatDateMask(value: string) {
  const digits = onlyDigits(value).slice(0, 8)
  if (digits.length <= 2) return digits
  if (digits.length <= 4) return `${digits.slice(0, 2)}/${digits.slice(2)}`
  return `${digits.slice(0, 2)}/${digits.slice(2, 4)}/${digits.slice(4)}`
}

function formatTimeMask(value: string, includeSeconds: boolean) {
  const maxLength = includeSeconds ? 6 : 4
  const digits = onlyDigits(value).slice(0, maxLength)

  if (digits.length <= 2) return digits
  if (!includeSeconds || digits.length <= 4) {
    return `${digits.slice(0, 2)}:${digits.slice(2)}`
  }

  return `${digits.slice(0, 2)}:${digits.slice(2, 4)}:${digits.slice(4)}`
}

function displayDateToIso(value: string) {
  const [day, month, year] = value.split("/")
  if (!day || !month || !year || year.length !== 4) return ""
  return `${year}-${month.padStart(2, "0")}-${day.padStart(2, "0")}`
}

function isoToDisplayDate(value: string) {
  const [year, month, day] = value.split("-")
  if (!day || !month || !year) return ""
  return `${day}/${month}/${year}`
}

function MaskedDateInput({
  className,
  onValueChange,
  placeholder = "29/04/2026",
  value,
  ...props
}: BaseMaskedInputProps) {
  const pickerRef = React.useRef<HTMLInputElement>(null)

  const openPicker = () => {
    const picker = pickerRef.current
    if (!picker) return

    if (typeof picker.showPicker === "function") {
      picker.showPicker()
      return
    }

    picker.click()
  }

  return (
    <div className="flex items-center gap-2">
      <Input
        {...props}
        className={cn("flex-1", className)}
        inputMode="numeric"
        maxLength={10}
        onChange={(event) => onValueChange(formatDateMask(event.target.value))}
        placeholder={placeholder}
        type="text"
        value={value}
      />
      <Button
        aria-label="Escolher data no calendário"
        size="icon"
        type="button"
        variant="outline"
        onClick={openPicker}
      >
        <CalendarDays />
      </Button>
      <input
        aria-hidden="true"
        className="sr-only"
        onChange={(event) => onValueChange(isoToDisplayDate(event.target.value))}
        ref={pickerRef}
        tabIndex={-1}
        type="date"
        value={displayDateToIso(value)}
      />
    </div>
  )
}

type MaskedTimeInputProps = BaseMaskedInputProps & {
  includeSeconds?: boolean
}

function MaskedTimeInput({
  includeSeconds = false,
  onValueChange,
  placeholder,
  value,
  ...props
}: MaskedTimeInputProps) {
  return (
    <Input
      {...props}
      inputMode="numeric"
      maxLength={includeSeconds ? 8 : 5}
      onChange={(event) => onValueChange(formatTimeMask(event.target.value, includeSeconds))}
      placeholder={placeholder ?? (includeSeconds ? "08:00:00" : "09:30")}
      type="text"
      value={value}
    />
  )
}

export { MaskedDateInput, MaskedTimeInput }