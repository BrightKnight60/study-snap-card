import { useState } from "react";
import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { Button } from "@/components/ui/button";
import { StudyMode } from "@/components/StudyMode";
import { CreateCardForm } from "@/components/CreateCardForm";
import { BookOpen, Plus, BarChart3 } from "lucide-react";

interface FlashcardData {
  id: string;
  front: string;
  back: string;
}

const Index = () => {
  const [cards, setCards] = useState<FlashcardData[]>([
    {
      id: "1",
      front: "What is the capital of France?",
      back: "Paris"
    },
    {
      id: "2", 
      front: "What does HTML stand for?",
      back: "HyperText Markup Language"
    }
  ]);
  const [mode, setMode] = useState<"study" | "create">("study");

  const addCard = (front: string, back: string) => {
    const newCard: FlashcardData = {
      id: Date.now().toString(),
      front,
      back,
    };
    setCards([...cards, newCard]);
    setMode("study");
  };

  const addCardsFromDocument = (newCards: Array<{front: string, back: string}>) => {
    const cardsWithIds: FlashcardData[] = newCards.map((card, index) => ({
      id: `${Date.now()}-${index}`,
      front: card.front,
      back: card.back,
    }));
    setCards(prevCards => [...prevCards, ...cardsWithIds]);
    setMode("study");
  };

  return (
    <div className="min-h-screen bg-background">
      <Toaster />
      <Sonner />
      
      {/* Header */}
      <header className="border-b bg-study-surface/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-primary flex items-center justify-center">
                <BookOpen className="w-5 h-5 text-primary-foreground" />
              </div>
              <div>
                <h1 className="text-2xl font-bold">FlashStudy</h1>
                <p className="text-sm text-muted-foreground">Interactive flashcard learning</p>
              </div>
            </div>
            
            <div className="flex items-center gap-2">
              <div className="flex items-center gap-1 text-sm text-muted-foreground mr-4">
                <BarChart3 className="w-4 h-4" />
                {cards.length} cards
              </div>
              <Button
                onClick={() => setMode(mode === "study" ? "create" : "study")}
                variant={mode === "create" ? "default" : "outline"}
                className="gap-2"
              >
                {mode === "create" ? (
                  <>
                    <BookOpen className="w-4 h-4" />
                    Study Mode
                  </>
                ) : (
                  <>
                    <Plus className="w-4 h-4" />
                    Create Cards
                  </>
                )}
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        {mode === "study" ? (
          <StudyMode cards={cards} onBackToCreate={() => setMode("create")} />
        ) : (
          <div className="max-w-2xl mx-auto">
            <CreateCardForm onAddCard={addCard} onAddCardsFromDocument={addCardsFromDocument} />
            
            {cards.length > 0 && (
              <div className="mt-8 text-center">
                <Button onClick={() => setMode("study")} className="gap-2">
                  <BookOpen className="w-4 h-4" />
                  Start Studying ({cards.length} cards)
                </Button>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
};

export default Index;
