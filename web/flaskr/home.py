
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)


@bp.route('/home', methods=('GET'))
def home():
    
    return render_template('base.html')