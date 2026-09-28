import { AuthTransitionProvider } from './components/AuthTransition'
import { AppRouter } from './routes/AppRouter'

function App() {
  return (
    <AuthTransitionProvider>
      <AppRouter />
    </AuthTransitionProvider>
  )
}

export default App