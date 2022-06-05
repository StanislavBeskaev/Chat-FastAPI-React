import React from 'react'
import {observer} from 'mobx-react-lite'
import {Button, Modal} from 'react-bootstrap'

import confirmDeleteContactModalStore from '../../stores/modals/confirmDeleteContactModalStore'
import contactStore from '../../stores/contactStore'


const ConfirmDeleteContactModal = () => {
  const {login} = confirmDeleteContactModalStore

  const handleYes = async () => {
    await contactStore.deleteContact(login)
    confirmDeleteContactModalStore.close()
  }

  const handleNo = () => {
    confirmDeleteContactModalStore.close()
  }

  return (
    <>
      <Modal.Body>
        <h6>Вы точно хотите удалить контакт {contactStore.getDisplayName(login)} ?</h6>
        <div className="d-flex m-4">
          <Button variant="danger" onClick={handleYes}>Да</Button>
          <Button variant="primary" className="ms-4" onClick={handleNo}>Нет</Button>
        </div>
      </Modal.Body>
    </>
  )
}

export default observer(ConfirmDeleteContactModal)