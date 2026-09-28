import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useState,
} from 'react'
import type { ReactNode } from 'react'
import { Box } from '@mui/material'
import { useNavigate } from 'react-router-dom'

type TransitionDirection = 'toLogin' | 'toRegister'
type TransitionPhase = 'idle' | 'fade' | 'cover' | 'reveal'

type AuthTransitionContextValue = {
  direction: TransitionDirection | null
  phase: TransitionPhase
  isTransitioning: boolean
  startAuthTransition: (
    target: string,
    direction: TransitionDirection,
  ) => void
}

const AuthTransitionContext =
  createContext<AuthTransitionContextValue | null>(null)

const wait = (milliseconds: number) =>
  new Promise<void>((resolve) => {
    window.setTimeout(resolve, milliseconds)
  })

type AuthTransitionProviderProps = {
  children: ReactNode
}

export function AuthTransitionProvider({
  children,
}: AuthTransitionProviderProps) {
  const navigate = useNavigate()

  const [phase, setPhase] =
    useState<TransitionPhase>('idle')

  const [direction, setDirection] =
    useState<TransitionDirection | null>(null)

  const startAuthTransition = useCallback(
    async (
      target: string,
      nextDirection: TransitionDirection,
    ) => {
      if (phase !== 'idle') {
        return
      }

      setDirection(nextDirection)

      // Primero se difumina el contenido.
      setPhase('fade')
      await wait(260)

      // Después la cortina cubre la pantalla.
      setPhase('cover')
      await wait(720)

      // La ruta cambia cuando la pantalla está cubierta.
      navigate(target)

      await wait(70)

      // La cortina se retira descubriendo la nueva página.
      setPhase('reveal')
      await wait(720)

      setPhase('idle')
      setDirection(null)
    },
    [navigate, phase],
  )

  const contextValue = useMemo(
    () => ({
      direction,
      phase,
      isTransitioning: phase !== 'idle',
      startAuthTransition,
    }),
    [direction, phase, startAuthTransition],
  )

  const getClipPath = () => {
    if (direction === 'toLogin') {
      if (phase === 'fade') {
        // Coincide con el panel izquierdo del registro.
        return 'inset(0 59% 0 0)'
      }

      if (phase === 'cover') {
        return 'inset(0 0 0 0)'
      }

      if (phase === 'reveal') {
        // Se retira hacia la izquierda.
        return 'inset(0 100% 0 0)'
      }
    }

    if (direction === 'toRegister') {
      if (phase === 'fade') {
        // Comienza en el extremo derecho.
        return 'inset(0 0 0 100%)'
      }

      if (phase === 'cover') {
        return 'inset(0 0 0 0)'
      }

      if (phase === 'reveal') {
        // Termina coincidiendo con el panel azul del registro.
        return 'inset(0 59% 0 0)'
      }
    }

    return 'inset(0 100% 0 0)'
  }

  return (
    <AuthTransitionContext.Provider value={contextValue}>
      {children}

      {phase !== 'idle' && (
        <Box
          aria-hidden="true"
          sx={{
            position: 'fixed',
            zIndex: 2000,
            inset: 0,
            pointerEvents: 'auto',
            clipPath: getClipPath(),
            background:
              'linear-gradient(145deg, #1557c8 0%, #2168d7 55%, #2d74e3 100%)',
            transition:
              phase === 'fade'
                ? 'none'
                : 'clip-path 720ms cubic-bezier(0.76, 0, 0.24, 1)',
            willChange: 'clip-path',
          }}
        />
      )}
    </AuthTransitionContext.Provider>
  )
}

// El proveedor y su hook forman una única API pública.
// eslint-disable-next-line react-refresh/only-export-components
export function useAuthTransition() {
  const context = useContext(AuthTransitionContext)

  if (!context) {
    throw new Error(
      'useAuthTransition debe utilizarse dentro de AuthTransitionProvider.',
    )
  }

  return context
}
