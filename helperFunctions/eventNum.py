class eventNum:
  count = 0

  @staticmethod
  def newEvent(self):
    self.count = self.count + 1
    return self.count
