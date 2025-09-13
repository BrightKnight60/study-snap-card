import { useState, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Progress } from "@/components/ui/progress";
import { Upload, FileText, Loader2 } from "lucide-react";
import { useToast } from "@/components/ui/use-toast";
import { ClaudeService } from "@/services/ClaudeService";

interface FileUploadProps {
  onCardsGenerated: (cards: { front: string; back: string }[]) => void;
  className?: string;
}

export function FileUpload({ onCardsGenerated, className }: FileUploadProps) {
  const [file, setFile] = useState<File | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [apiKey, setApiKey] = useState("");
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { toast } = useToast();

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = event.target.files?.[0];
    if (selectedFile) {
      setFile(selectedFile);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      toast({
        title: "No file selected",
        description: "Please select a file to process",
        variant: "destructive",
      });
      return;
    }

    if (!apiKey.trim()) {
      toast({
        title: "API Key required",
        description: "Please enter your Claude API key",
        variant: "destructive",
      });
      return;
    }

    setIsProcessing(true);
    setProgress(20);

    try {
      // Save API key for future use
      ClaudeService.saveApiKey(apiKey);
      setProgress(40);

      // Read file content
      const fileContent = await readFileContent(file);
      setProgress(60);

      // Process with Claude
      const generatedCards = await ClaudeService.generateFlashcards(fileContent);
      setProgress(80);

      if (generatedCards.length > 0) {
        onCardsGenerated(generatedCards);
        toast({
          title: "Success!",
          description: `Generated ${generatedCards.length} flashcards from your document`,
        });
        setFile(null);
        if (fileInputRef.current) {
          fileInputRef.current.value = "";
        }
      } else {
        toast({
          title: "No cards generated",
          description: "Could not extract questions and answers from the document",
          variant: "destructive",
        });
      }
    } catch (error) {
      toast({
        title: "Processing failed",
        description: error instanceof Error ? error.message : "Failed to process document",
        variant: "destructive",
      });
    } finally {
      setIsProcessing(false);
      setProgress(100);
      setTimeout(() => setProgress(0), 1000);
    }
  };

  const readFileContent = (file: File): Promise<string> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = (e) => resolve(e.target?.result as string);
      reader.onerror = reject;
      reader.readAsText(file);
    });
  };

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Upload className="w-5 h-5 text-accent" />
          Generate from Document
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-2">
          <Label htmlFor="apiKey">Claude API Key</Label>
          <Input
            id="apiKey"
            type="password"
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
            placeholder="Enter your Claude API key..."
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="file">Upload Document</Label>
          <div className="flex items-center gap-2">
            <Input
              ref={fileInputRef}
              id="file"
              type="file"
              accept=".txt,.md,.pdf,.docx"
              onChange={handleFileSelect}
              className="flex-1"
            />
            {file && (
              <div className="flex items-center gap-1 text-sm text-muted-foreground">
                <FileText className="w-4 h-4" />
                {file.name}
              </div>
            )}
          </div>
        </div>

        {isProcessing && (
          <div className="space-y-2">
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Loader2 className="w-4 h-4 animate-spin" />
              Processing document...
            </div>
            <Progress value={progress} className="w-full" />
          </div>
        )}

        <Button
          onClick={handleUpload}
          disabled={!file || !apiKey.trim() || isProcessing}
          className="w-full"
        >
          {isProcessing ? (
            <>
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              Generating Flashcards...
            </>
          ) : (
            <>
              <Upload className="w-4 h-4 mr-2" />
              Generate Flashcards
            </>
          )}
        </Button>

        <p className="text-xs text-muted-foreground">
          Supports .txt, .md, .pdf, and .docx files. The AI will extract key concepts and create question-answer pairs.
        </p>
      </CardContent>
    </Card>
  );
}