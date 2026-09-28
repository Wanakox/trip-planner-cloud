import type { PropsWithChildren } from 'react'
import { Box, Paper, Typography } from '@mui/material'

type AuthCardProps = PropsWithChildren<{
  title: string
  subtitle: string
}>

export function AuthCard({ title, subtitle, children }: AuthCardProps) {
  return (
    <Paper elevation={0} sx={{ width: '100%', maxWidth: 520, borderRadius: '24px', boxShadow: '0 8px 24px rgba(11, 26, 47, 0.10)', p: { xs: 3, sm: 6 } }}>
      <Typography
        component="h1"
        sx={{
          fontSize: { xs: 28, sm: 32 },
          lineHeight: 1.3,
          fontWeight: 800,
        }}
      >
        {title}
      </Typography>

      <Typography
        color="text.secondary"
        sx={{
          mt: 0.5,
          fontSize: 15,
        }}
      >
        {subtitle}
      </Typography>
      <Box sx={{ mt: 4 }}>{children}</Box>
    </Paper>
  )
}
