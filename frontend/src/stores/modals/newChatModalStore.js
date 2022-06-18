import {makeAutoObservable} from "mobx"


class NewChatModalStore {
  show = false
  name = ''

  constructor() {
    makeAutoObservable(this)
    console.log("Создан NewChatModalStore")
  }

  open() {
    //  TODO установка начальных значений
    this.name = ''
    this.show = true
  }

  close() {
    this.show = false
  }
}

export default new NewChatModalStore()
