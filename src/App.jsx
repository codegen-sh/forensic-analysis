import Header from './components/Header'
import CriticalFindings from './components/CriticalFindings'
import StatsGrid from './components/StatsGrid'
import EvidenceGrid from './components/EvidenceGrid'
import Methodology from './components/Methodology'
import CallToAction from './components/CallToAction'
import LegalImplications from './components/LegalImplications'
import Footer from './components/Footer'
import './styles/globals.css'

function App() {
  return (
    <div className="container">
      <Header />
      <CriticalFindings />
      <StatsGrid />
      <EvidenceGrid />
      <Methodology />
      <CallToAction />
      <LegalImplications />
      <Footer />
    </div>
  )
}

export default App
