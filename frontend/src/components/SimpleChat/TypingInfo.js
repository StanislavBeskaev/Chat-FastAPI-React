import React from 'react'

export default function TypingInfo({ logins }) {
  if (logins.length === 0) return null

  const typingText = logins.length === 1 ? 'печатает' : 'печатают'

  return (
    <div className="ps-2 small text-primary">
      {`${logins.join(', ')} ${typingText}...`}
    </div>
  )
}