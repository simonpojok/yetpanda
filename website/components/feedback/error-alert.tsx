import { AlertCircle } from "lucide-react";

import { Alert, AlertDescription } from "@/components/ui/alert";

export function ErrorAlert({ message }: { message: string }) {
  return (
    <Alert variant="destructive" className="rounded-[4px]">
      <AlertCircle className="size-4" />
      <AlertDescription>{message}</AlertDescription>
    </Alert>
  );
}
