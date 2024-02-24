function AI_ANALYZE(title, abstract) {
  const scriptProperties = PropertiesService.getScriptProperties();
  const apiKey = scriptProperties.getProperty('OPENAI_API_KEY'); 
  const url = 'https://api.openai.com/v1/chat/completions';

  const data = {
    model: 'gpt-3.5-turbo',
    "messages": [
      {
        "role": "system",
        "content": `I'll give you a scientific article, apply to it inclusion and exclusion criteria:

Specific Exclusion Criteria:

1. Non-psychophysiological Focus: Eliminate literature focused solely on linguistic cues, behavioral analysis, or purely subjective/interpretive methods of emotion assessment.

2. Studies Outside CMC: Exclude research focusing on non-digital, face-to-face communication settings unless there is a strong argument for transferability to CMC.

3. Outdated Technology: Remove articles relying on technology or methodologies rendered significantly obsolete in recent years.

4. Lack of Empirical Measurement: Filter out works offering purely theoretical models or opinion pieces that lack rigorous empirical evaluation of emotion-related cue measurement.

5. Not grown up participants

6. Research evolves around mental ilness

Specific Inclusion Criteria

1. Direct Examination of Emotion Cues: Include studies that clearly define and address specific psychophysiological emotion cues (e.g., facial expressions, heart rate variability, electrodermal activity, etc.).

2. Variety of CMC Contexts: Prioritize literature examining diverse CMC environments (e.g., text-based chat, video conferencing, virtual reality, etc.).

3. Empirical Evaluation of Measurement: Include studies with clear methodology for measuring emotion-related cues. Ideally, look for those comparing multiple measurement approaches.

4. Quantitative Measures: Favor research quantifying emotion-related cues, providing insights suitable for ranking and categorization.
`
      },
      {
        "role": "user",
        "content": title + " " + abstract
      }
    ]
  };

  const options = {
    method: 'post',
    contentType: 'application/json',
    headers: {
      'Authorization': `Bearer ${apiKey}`,
      'OpenAI-Beta': 'assistants=v1',
    },
    payload: JSON.stringify(data),
    muteHttpExceptions: true
  };

  try {
    const response = UrlFetchApp.fetch(url, options);
    const jsonResponse = JSON.parse(response.getContentText());

    if (response.getResponseCode() !== 200) {
      throw new Error(`Error: ${jsonResponse.error}`);
    }

    return jsonResponse.choices[0].message.content;
  } catch (error) {
    Logger.log(error);
    return `Error: ${error.message}`;
  }
}
