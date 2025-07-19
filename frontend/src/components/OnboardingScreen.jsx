import React, { useState } from 'react'
import { View, Text, TouchableOpacity } from 'react-native'

const questions = [
  {
    id: 'style',
    text: "What's your investing style?",
    options: ['Value Hunter', 'Momentum', 'Long-Term', 'Speculator'],
  },
  {
    id: 'sector',
    text: 'Preferred sectors?',
    options: ['Tech', 'Finance', 'Energy', 'Healthcare'],
  },
  {
    id: 'risk',
    text: 'Risk tolerance?',
    options: ['Low', 'Medium', 'High', 'Very High'],
  },
  {
    id: 'experience',
    text: 'Experience level?',
    options: ['Beginner', 'Intermediate', 'Advanced', 'Expert'],
  },
]

export default function OnboardingScreen({ onComplete }) {
  const [answers, setAnswers] = useState({})
  const handleSelect = (qid, option) => {
    setAnswers(prev => ({ ...prev, [qid]: option }))
  }
  const allAnswered = questions.every(q => answers[q.id])

  return (
    <View>
      {questions.map(q => (
        <View key={q.id}>
          <Text>{q.text}</Text>
          {q.options.map(option => (
            <TouchableOpacity
              key={option}
              onPress={() => handleSelect(q.id, option)}
            >
              <Text>
                {answers[q.id] === option ? '🔘' : '⚪'} {option}
              </Text>
            </TouchableOpacity>
          ))}
        </View>
      ))}
      {allAnswered && (
        <TouchableOpacity onPress={() => onComplete?.(answers)}>
          <Text>Finish</Text>
        </TouchableOpacity>
      )}
    </View>
  )
}
