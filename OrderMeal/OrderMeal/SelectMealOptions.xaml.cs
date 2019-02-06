using System;
using System.Collections.Generic;

using Xamarin.Forms;

namespace OrderMeal
{
    public partial class SelectMealOptions : ContentPage
    {
        public SelectMealOptions()
        {
            InitializeComponent();

        }

        async void Handle_Clicked(object sender, System.EventArgs e)
        {
            var secondPage = new CheckOutPage(optionOne.Text, optionTwo.Text);
            await Navigation.PushAsync(secondPage);
        }
    }
}
