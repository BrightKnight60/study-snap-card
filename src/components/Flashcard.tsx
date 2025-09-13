import { useState } from "react";
import { Card } from "@/components/ui/card";
import { cn } from "@/lib/utils";

interface FlashcardProps {
  front: string;
  back: string;
  className?: string;
}

export function Flashcard({ front, back, className }: FlashcardProps) {
  const [isFlipped, setIsFlipped] = useState(false);

  const handleFlip = () => {
    setIsFlipped(!isFlipped);
  };

  return (
    <div className={cn("perspective-1000", className)}>
      <div
        className={cn(
          "relative w-full h-80 cursor-pointer transform-style-3d transition-transform duration-700 ease-in-out",
          isFlipped ? "rotate-y-180" : ""
        )}
        onClick={handleFlip}
      >
        {/* Front of card */}
        <Card className={cn(
          "absolute inset-0 w-full h-full backface-hidden",
          "bg-gradient-surface shadow-card hover:shadow-elevated transition-all duration-300",
          "border-0 flex items-center justify-center p-8"
        )}>
          <div className="text-center">
            <div className="text-2xl font-semibold mb-4 text-foreground leading-relaxed">
              {front}
            </div>
            <div className="text-sm text-muted-foreground">
              Click to reveal answer
            </div>
          </div>
        </Card>

        {/* Back of card */}
        <Card className={cn(
          "absolute inset-0 w-full h-full backface-hidden rotate-y-180",
          "bg-gradient-primary shadow-card hover:shadow-elevated transition-all duration-300",
          "border-0 flex items-center justify-center p-8"
        )}>
          <div className="text-center">
            <div className="text-2xl font-semibold text-primary-foreground leading-relaxed">
              {back}
            </div>
            <div className="text-sm text-primary-foreground/80 mt-4">
              Click to flip back
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}