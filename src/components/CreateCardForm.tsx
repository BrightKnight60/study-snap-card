import { useState, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useToast } from "@/hooks/use-toast";
import { Plus, Upload, FileText, Loader2 } from "lucide-react";
import { getApiUrl } from "@/lib/api";

interface CreateCardFormProps {
  onAddCard: (front: string, back: string) => void;
  onAddCardsFromDocument: (cards: Array<{front: string, back: string}>) => void;
  className?: string;
}

export function CreateCardForm({ onAddCard, onAddCardsFromDocument, className }: CreateCardFormProps) {
  const [front, setFront] = useState("");
  const [back, setBack] = useState("");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { toast } = useToast();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (front.trim() && back.trim()) {
      onAddCard(front.trim(), back.trim());
      setFront("");
      setBack("");
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      // Validate file size (5MB limit)
      const maxSize = 5 * 1024 * 1024; // 5MB
      if (file.size > maxSize) {
        toast({
          title: "File too large",
          description: "Please select a file smaller than 5MB.",
          variant: "destructive",
        });
        return;
      }

      // Validate file type
      const allowedTypes = ['text/plain', 'application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
      if (!allowedTypes.includes(file.type)) {
        toast({
          title: "Unsupported file type",
          description: "Please select a TXT, PDF, DOC, or DOCX file.",
          variant: "destructive",
        });
        return;
      }

      setSelectedFile(file);
    }
  };

  const handleFileUpload = async () => {
    if (!selectedFile) return;

    setIsUploading(true);
    const formData = new FormData();
    formData.append('file', selectedFile);

    console.log('Uploading to:', getApiUrl('/upload')); // Debug log

    try {
      const response = await fetch(getApiUrl('/upload'), {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      if (response.ok) {
        toast({
          title: "Success!",
          description: `Generated ${data.flashcards_count} flashcards from ${selectedFile.name}`,
        });

        // Add the generated flashcards to the frontend
        onAddCardsFromDocument(data.flashcards);

        // Reset file selection
        setSelectedFile(null);
        if (fileInputRef.current) {
          fileInputRef.current.value = '';
        }
      } else {
        toast({
          title: "Upload failed",
          description: data.error || "An error occurred while processing your file.",
          variant: "destructive",
        });
      }
    } catch (error) {
      toast({
        title: "Upload failed",
        description: "Could not connect to the server. Make sure the backend is running.",
        variant: "destructive",
      });
    } finally {
      setIsUploading(false);
    }
  };

  const clearFile = () => {
    setSelectedFile(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Plus className="w-5 h-5 text-accent" />
          Create Flashcards
        </CardTitle>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue="manual" className="w-full">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="manual">Manual Entry</TabsTrigger>
            <TabsTrigger value="document">From Document</TabsTrigger>
          </TabsList>

          <TabsContent value="manual" className="space-y-4 mt-6">
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
                <Plus className="w-4 h-4 mr-2" />
                Add Flashcard
              </Button>
            </form>
          </TabsContent>

          <TabsContent value="document" className="space-y-4 mt-6">
            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="file-upload">Upload Document</Label>
                <div className="flex flex-col gap-4">
                  <Input
                    ref={fileInputRef}
                    id="file-upload"
                    type="file"
                    accept=".txt,.pdf,.doc,.docx"
                    onChange={handleFileSelect}
                    disabled={isUploading}
                  />

                  {selectedFile && (
                    <div className="flex items-center justify-between p-3 bg-muted rounded-lg">
                      <div className="flex items-center gap-2">
                        <FileText className="w-4 h-4" />
                        <span className="text-sm font-medium">{selectedFile.name}</span>
                        <span className="text-xs text-muted-foreground">
                          ({(selectedFile.size / 1024).toFixed(1)} KB)
                        </span>
                      </div>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={clearFile}
                        disabled={isUploading}
                      >
                        ×
                      </Button>
                    </div>
                  )}

                  <div className="text-xs text-muted-foreground">
                    Supported formats: TXT, PDF, DOC, DOCX (max 5MB)
                  </div>

                  <Button
                    onClick={handleFileUpload}
                    disabled={!selectedFile || isUploading}
                    className="w-full"
                  >
                    {isUploading ? (
                      <>
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                        Processing...
                      </>
                    ) : (
                      <>
                        <Upload className="w-4 h-4 mr-2" />
                        Generate Flashcards
                      </>
                    )}
                  </Button>
                </div>
              </div>

              {isUploading && (
                <div className="text-center text-sm text-muted-foreground">
                  Claude is analyzing your document and creating flashcards...
                </div>
              )}
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
}