from smarty.extensions import db


class BaseModel(db.Model):
    __abstract__ = True

    def add(self, autoflush: bool = True):
        """Add the model to the database session.

        :param autoflush: Whether to flush the session after the
            update. Will populate auto-generated columns in the Model
            object.
        """
        db.session.add(self)

        if autoflush:
            db.session.flush()

    def update(self, autoflush: bool = True, **kwargs):
        """Update certain fields the model, and add it to the session.

        :param autoflush: Whether to flush the session after the
            update. Will populate auto-generated columns in the Model
            object.
        """
        for attr, value in kwargs.items():
            setattr(self, attr, value)

        self.add(autoflush)

    def delete(self):
        """Delete the model from the database."""
        # TODO make this a soft-delete, add separate `hard_delete()`
        db.session.delete(self)

    # TODO add auditing columns to base model
