import { Route, Routes } from 'react-router-dom'

import { DashboardLayout } from '../components/layout/DashboardLayout'
import { CreateTripPage } from '../pages/CreateTripPage'
import { EditTripPage } from '../pages/EditTripPage'
import { FlightSearchPage } from '../pages/FlightSearchPage'
import { HomePage } from '../pages/HomePage'
import { LoginPage } from '../pages/LoginPage'
import { ProfilePage } from '../pages/ProfilePage'
import { RegisterPage } from '../pages/RegisterPage'
import { TripDetailsPage } from '../pages/TripDetailsPage'
import { TripsPage } from '../pages/TripsPage'
import { ProtectedRoute } from './ProtectedRoute'

export function AppRouter() {
  return (
    <Routes>
      <Route
        element={<HomePage />}
        path="/"
      />

      <Route
        element={<RegisterPage />}
        path="/registro"
      />

      <Route
        element={<LoginPage />}
        path="/iniciar-sesion"
      />

      <Route element={<ProtectedRoute />}>
        <Route element={<DashboardLayout />}>
          <Route
            element={<TripsPage />}
            path="/viajes"
          />

          <Route
            element={<CreateTripPage />}
            path="/viajes/nuevo"
          />

          <Route
            element={<TripDetailsPage />}
            path="/viajes/:tripId"
          />

          <Route
            element={<EditTripPage />}
            path="/viajes/:tripId/editar"
          />

          <Route
            element={<FlightSearchPage />}
            path="/buscar-vuelos"
          />

          <Route
            element={<ProfilePage />}
            path="/perfil"
          />
        </Route>
      </Route>
    </Routes>
  )
}
