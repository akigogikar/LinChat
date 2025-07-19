import { useState } from 'react'
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Stepper,
  Step,
  StepLabel,
  Typography,
  Box,
  TextField,
  Tooltip,
} from '@mui/material'

export default function Onboarding({ open, onClose }) {
  const steps = [
    {
      label: 'Upload Files',
      content: (
        <Box sx={{ textAlign: 'center' }}>
          <Typography sx={{ mb: 2 }}>
            Upload your documents to begin chatting with your data.
          </Typography>
          <Tooltip title="Select a file and click Upload">
            <span>
              <Button variant="contained" disabled>
                Upload
              </Button>
            </span>
          </Tooltip>
        </Box>
      ),
    },
    {
      label: 'Ask Questions',
      content: (
        <Box sx={{ textAlign: 'center' }}>
          <Typography sx={{ mb: 2 }}>
            Once uploaded, ask questions about the content.
          </Typography>
          <TextField
            disabled
            placeholder="Type your question"
            size="small"
            sx={{ mr: 1 }}
          />
          <Tooltip title="Send your question to get an answer">
            <span>
              <Button variant="contained" disabled>
                Send
              </Button>
            </span>
          </Tooltip>
        </Box>
      ),
    },
    {
      label: 'Export Results',
      content: (
        <Box sx={{ textAlign: 'center' }}>
          <Typography sx={{ mb: 2 }}>
            Save or share your results with your team.
          </Typography>
          <Tooltip title="Generate a PDF from your conversation">
            <span>
              <Button variant="contained" disabled>
                Export PDF
              </Button>
            </span>
          </Tooltip>
        </Box>
      ),
    },
  ]

  const [activeStep, setActiveStep] = useState(0)

  const handleNext = () => {
    setActiveStep(prev => Math.min(prev + 1, steps.length - 1))
  }

  const handleBack = () => {
    setActiveStep(prev => Math.max(prev - 1, 0))
  }

  const handleClose = () => {
    if (onClose) onClose()
  }

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
      <DialogTitle>Welcome to LinChat</DialogTitle>
      <DialogContent>
        <Stepper activeStep={activeStep} alternativeLabel sx={{ mb: 2 }}>
          {steps.map(step => (
            <Step key={step.label}>
              <StepLabel>{step.label}</StepLabel>
            </Step>
          ))}
        </Stepper>
        <Box sx={{ minHeight: 140 }}>{steps[activeStep].content}</Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={handleClose}>Skip</Button>
        {activeStep > 0 && (
          <Button onClick={handleBack}>Back</Button>
        )}
        {activeStep < steps.length - 1 ? (
          <Button variant="contained" onClick={handleNext}>
            Next
          </Button>
        ) : (
          <Button variant="contained" onClick={handleClose}>
            Finish
          </Button>
        )}
      </DialogActions>
    </Dialog>
  )
}
