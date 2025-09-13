export interface FlashcardData {
  front: string;
  back: string;
}

export class ClaudeService {
  private static API_KEY_STORAGE_KEY = 'claude_api_key';
  private static BASE_URL = 'https://api.anthropic.com/v1/messages';

  static saveApiKey(apiKey: string): void {
    localStorage.setItem(this.API_KEY_STORAGE_KEY, apiKey);
  }

  static getApiKey(): string | null {
    return localStorage.getItem(this.API_KEY_STORAGE_KEY);
  }

  static async generateFlashcards(content: string): Promise<FlashcardData[]> {
    const apiKey = this.getApiKey();
    if (!apiKey) {
      throw new Error('API key not found');
    }

    try {
      const response = await fetch(this.BASE_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-api-key': apiKey,
          'anthropic-version': '2023-06-01'
        },
        body: JSON.stringify({
          model: 'claude-3-sonnet-20240229',
          max_tokens: 4000,
          messages: [
            {
              role: 'user',
              content: `Please analyze the following text and create flashcards for studying. Extract key concepts, definitions, facts, and important information. Format your response as a JSON array where each flashcard has "front" (question/term) and "back" (answer/definition) properties.

Rules:
- Create 5-15 flashcards depending on content length
- Front should be clear, concise questions or terms
- Back should be comprehensive but focused answers
- Focus on the most important concepts
- Avoid overly simple or overly complex cards
- Ensure questions test understanding, not just memorization

Text to analyze:
${content}

Response format:
[
  {"front": "What is...?", "back": "The answer is..."},
  {"front": "Define term", "back": "Term means..."}
]`
            }
          ]
        })
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error?.message || `HTTP ${response.status}: Failed to generate flashcards`);
      }

      const data = await response.json();
      const content_text = data.content?.[0]?.text;
      
      if (!content_text) {
        throw new Error('No response content received from Claude');
      }

      // Extract JSON from response
      const jsonMatch = content_text.match(/\[[\s\S]*\]/);
      if (!jsonMatch) {
        throw new Error('Could not find valid JSON in Claude response');
      }

      const flashcards = JSON.parse(jsonMatch[0]);
      
      // Validate flashcards format
      if (!Array.isArray(flashcards)) {
        throw new Error('Response is not a valid flashcard array');
      }

      const validFlashcards = flashcards.filter(card => 
        card && 
        typeof card === 'object' && 
        typeof card.front === 'string' && 
        typeof card.back === 'string' &&
        card.front.trim() !== '' && 
        card.back.trim() !== ''
      );

      if (validFlashcards.length === 0) {
        throw new Error('No valid flashcards found in response');
      }

      return validFlashcards;
    } catch (error) {
      if (error instanceof Error) {
        throw error;
      }
      throw new Error('Failed to generate flashcards');
    }
  }
}