# Migration Guide: OpenAI to Google Gemini

This guide helps you migrate from OpenAI to Google Gemini API.

## Overview

The Technical Documentation Assistant has been updated to use Google's Gemini AI instead of OpenAI. This change provides:

- **Cost efficiency**: Gemini offers competitive pricing
- **Performance**: Gemini 1.5 Pro provides excellent capabilities
- **Flexibility**: Access to Google's AI ecosystem

## What Changed

### API Provider
- **Before**: OpenAI (GPT-4)
- **After**: Google Gemini (gemini-1.5-pro)

### Embeddings
- **Before**: OpenAI text-embedding-3-small
- **After**: Google models/embedding-001

### Dependencies
- **Removed**: `langchain-openai`, `openai`
- **Added**: `langchain-google-genai`, `google-generativeai`

## Migration Steps

### 1. Get Google API Key

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the generated API key

### 2. Update Environment Variables

Update your `.env` file:

```bash
# Old
OPENAI_API_KEY=sk-...

# New
GOOGLE_API_KEY=AIza...
```

### 3. Install Updated Dependencies

```bash
# Recommended: Create a fresh virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install updated requirements
pip install -r requirements.txt
```

### 4. Reset Vector Database (Important!)

The embeddings have changed, so you need to rebuild the vector database:

```bash
# Delete the existing database
rm -rf chroma_db/

# The database will be automatically rebuilt on first run
```

### 5. Test the Application

```bash
streamlit run app.py
```

## Configuration Changes

### config.py

The following configuration variables were updated:

| Old Variable | New Variable | Default Value |
|-------------|--------------|---------------|
| `OPENAI_API_KEY` | `GOOGLE_API_KEY` | From .env |
| `OPENAI_MODEL` | `GOOGLE_MODEL` | `gemini-1.5-pro` |
| `EMBEDDING_MODEL` | `EMBEDDING_MODEL` | `models/embedding-001` |

### Model Capabilities

**Gemini 1.5 Pro Features:**
- Large context window (up to 1M tokens)
- Multimodal capabilities
- Competitive performance with GPT-4
- Built-in safety filters

## Known Differences

### Tool Calling

Google Gemini has different tool calling capabilities compared to OpenAI. The implementation includes:

- Fallback mechanism for tool calling
- Graceful degradation if tools aren't supported
- Logging of tool-related warnings

### Response Format

Gemini may format responses slightly differently:
- Code blocks may use different formatting
- JSON responses may have different structure
- Error messages will reference Google APIs

## Troubleshooting

### Issue: "GOOGLE_API_KEY not found"

**Solution**: 
1. Ensure `.env` file exists in the project root
2. Verify the key is correctly formatted: `GOOGLE_API_KEY=AIza...`
3. Restart the application after updating `.env`

### Issue: Embeddings Error

**Solution**:
1. Delete the `chroma_db/` directory
2. Restart the application to rebuild with new embeddings

### Issue: Tool Calling Not Working

**Solution**:
- This is expected with Gemini in some cases
- The system will fall back to basic responses
- Check logs for specific error messages

### Issue: Rate Limiting

**Solution**:
- Google has different rate limits than OpenAI
- Check [Google AI Studio](https://makersuite.google.com/) for your quota
- Consider upgrading to a paid tier if needed

## API Key Security

### Best Practices

1. **Never commit API keys** to version control
2. **Use environment variables** for all sensitive data
3. **Rotate keys regularly** for security
4. **Monitor usage** in Google AI Studio

### .gitignore

Ensure your `.gitignore` includes:
```
.env
*.log
chroma_db/
```

## Cost Comparison

### Google Gemini Pricing (as of 2024)

- **Gemini 1.5 Pro**: Free tier available, then pay-per-use
- **Embeddings**: Included in API usage
- **Rate Limits**: Generous free tier

### Monitoring Usage

Monitor your usage at:
- [Google AI Studio](https://makersuite.google.com/)
- Check the "Usage" section for detailed metrics

## Rollback (If Needed)

If you need to rollback to OpenAI:

1. Checkout the previous version of the code
2. Restore your OpenAI API key in `.env`
3. Delete `chroma_db/` and rebuild
4. Run `pip install -r requirements.txt`

## Support

For issues:
1. Check this migration guide
2. Review `chatbot.log` for errors
3. Verify API key is valid in Google AI Studio
4. Ensure all dependencies are installed correctly

## Additional Resources

- [Google AI Documentation](https://ai.google.dev/docs)
- [Gemini API Quickstart](https://ai.google.dev/tutorials/python_quickstart)
- [LangChain Google Integration](https://python.langchain.com/docs/integrations/platforms/google)
- [Google AI Studio](https://makersuite.google.com/)

---

**Migration completed successfully!** 🎉

Your Technical Documentation Assistant is now powered by Google Gemini.
