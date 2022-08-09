import React from 'react'
import {observer} from 'mobx-react-lite'
import {Button, Modal} from 'react-bootstrap'

import confirmDeleteModalStore from '../../stores/modals/confirmDeleteModalStore'


const ConfirmDeleteModal = () => {
  const {text, onYes, onNo} = confirmDeleteModalStore
  return (
    <Modal.Body>
      <h6>{text}</h6>
      <div className="d-flex m-4">
        <Button variant="danger" onClick={() => onYes()}>Да</Button>
        <Button variant="primary" className="ms-4" onClick={() => onNo()}>Нет</Button>
      </div>
    </Modal.Body>
  )
}

export default observer(ConfirmDeleteModal)
