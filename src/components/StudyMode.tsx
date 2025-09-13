import { useState } from "react";
import { Flashcard } from "./Flashcard";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { ChevronLeft, ChevronRight, RotateCcw } from "lucide-react";

interface FlashcardData {
  id: string;
  front: string;
  back: string;
}

interface StudyModeProps {
  cards: FlashcardData[];
  onBackToCreate: () => void;
}

export function StudyMode({ cards, onBackToCreate }: StudyModeProps) {
  const [currentIndex, setCurrentIndex] = useState(0);

  if (cards.length === 0) {
    return (
      <div className="max-w-2xl mx-auto text-center py-12">
        <Card className="p-8">
          <CardContent className="space-y-4">
            <div className="text-6xl mb-4">📚</div>
            <h2 className="text-2xl font-semibold">No flashcards yet!</h2>
            <p className="text-muted-foreground">
              Create your first flashcard to start studying.
            </p>
            <Button onClick={onBackToCreate} className="mt-4">
              Create Flashcard
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  const currentCard = cards[currentIndex];

  const nextCard = () => {
    setCurrentIndex((prev) => (prev + 1) % cards.length);
  };

  const prevCard = () => {
    setCurrentIndex((prev) => (prev - 1 + cards.length) % cards.length);
  };

  const resetProgress = () => {
    setCurrentIndex(0);
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      {/* Progress indicator */}
      <div className="text-center">
        <div className="text-sm text-muted-foreground mb-2">
          Card {currentIndex + 1} of {cards.length}
        </div>
        <div className="w-full bg-secondary rounded-full h-2">
          <div
            className="bg-gradient-primary h-2 rounded-full transition-all duration-300"
            style={{ width: `${((currentIndex + 1) / cards.length) * 100}%` }}
          />
        </div>
      </div>

      {/* Flashcard */}
      <Flashcard
        front={currentCard.front}
        back={currentCard.back}
        key={currentCard.id} // Force re-render to reset flip state
      />

      {/* Navigation controls */}
      <div className="flex items-center justify-between">
        <Button
          onClick={prevCard}
          variant="outline"
          size="sm"
          disabled={cards.length <= 1}
        >
          <ChevronLeft className="w-4 h-4 mr-1" />
          Previous
        </Button>

        <div className="flex gap-2">
          <Button onClick={resetProgress} variant="outline" size="sm">
            <RotateCcw className="w-4 h-4 mr-1" />
            Reset
          </Button>
          <Button onClick={onBackToCreate} variant="outline" size="sm">
            Add Cards
          </Button>
        </div>

        <Button
          onClick={nextCard}
          variant="outline"
          size="sm"
          disabled={cards.length <= 1}
        >
          Next
          <ChevronRight className="w-4 h-4 ml-1" />
        </Button>
      </div>
    </div>
  );
}