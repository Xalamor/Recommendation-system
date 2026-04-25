import { Route, Routes } from 'react-router-dom'
import Navbar from './components/Navbar'
import Home from './pages/Home'
import Dataset from './pages/Dataset'
import Model from './pages/Model'
import Demo from './pages/Demo'
import Results from './pages/Results'
import Business from './pages/Business'

export default function App() {
  return (
    <>
      <Navbar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/dataset" element={<Dataset />} />
        <Route path="/model" element={<Model />} />
        <Route path="/demo" element={<Demo />} />
        <Route path="/results" element={<Results />} />
        <Route path="/business" element={<Business />} />
      </Routes>
    </>
  )
}
