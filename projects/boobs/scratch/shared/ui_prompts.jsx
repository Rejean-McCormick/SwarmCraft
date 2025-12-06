import React from 'react';

// Simple UI to list and create prompts
function PromptsList({ prompts }) {
  return (
    <div>
      <h2>Prompts</h2>
      <ul>
        {prompts?.map(p => (
          <li key={p.id}>{p.content}</li>
        ))}
      </ul>
    </div>
  );
}

export default PromptsList;
