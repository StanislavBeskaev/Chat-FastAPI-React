import React from 'react'
import {Spinner} from 'react-bootstrap'

const Loader = () => {
  return (
    <div className="m-5">
      <Spinner animation="border" variant="primary" className="me-2" />
      Загрузка данных
    </div>

  )
}

export default Loader