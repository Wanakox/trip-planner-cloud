import { render, screen } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { describe, expect, it, vi } from 'vitest'

import { ProtectedRoute } from './ProtectedRoute'

vi.mock('../utils/authSession', () => ({
  clearStoredSession: vi.fn(),
  hasValidAccessToken: vi.fn(),
}))

import { clearStoredSession, hasValidAccessToken } from '../utils/authSession'

function renderRoute() {
  return render(<MemoryRouter initialEntries={['/viajes']}><Routes>
    <Route element={<ProtectedRoute />}><Route path="/viajes" element={<div>Contenido privado</div>} /></Route>
    <Route path="/iniciar-sesion" element={<div>Inicio de sesión</div>} />
  </Routes></MemoryRouter>)
}

describe('ProtectedRoute', () => {
  it('muestra la ruta protegida con sesión válida', () => {
    vi.mocked(hasValidAccessToken).mockReturnValue(true)
    renderRoute()
    expect(screen.getByText('Contenido privado')).toBeInTheDocument()
  })

  it('limpia la sesión y redirige cuando ha caducado', () => {
    vi.mocked(hasValidAccessToken).mockReturnValue(false)
    renderRoute()
    expect(clearStoredSession).toHaveBeenCalledOnce()
    expect(screen.getByText('Inicio de sesión')).toBeInTheDocument()
  })
})
