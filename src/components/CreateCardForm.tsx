import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Plus } from "lucide-react";

interface CreateCardFormProps {
  onAddCard: (front: string, back: string) => void;
  className?: string;
}

export function CreateCardForm({ onAddCard, className }: CreateCardFormProps) {
  const [front, setFront] = useState("");
  const [back, setBack] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (front.trim() && back.trim()) {
      onAddCard(front.trim(), back.trim());
      setFront("");
      setBack("");
    }
  };

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Plus className="w-5 h-5 text-accent" />
          Create New Flashcard
        </CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="front">Front (Question)</Label>
            <Textarea
              id="front"
              value={front}
              onChange={(e) => setFront(e.target.value)}
              placeholder="Enter the question or term..."
              className="min-h-[100px] resize-none"
            />
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="back">Back (Answer)</Label>
            <Textarea
              id="back"
              value={back}
              onChange={(e) => setBack(e.target.value)}
              placeholder="Enter the answer or definition..."
              className="min-h-[100px] resize-none"
            />
          </div>

          <Button
            type="submit"
            className="w-full"
            disabled={!front.trim() || !back.trim()}
          >
            Add Flashcard
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}